#include <atomic>
#include <cassert>
#include <error.h>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>
#include <vector>

class LinkLock {
public:
  std::string _lockfile;
  std::string _linkfile;
  LinkLock(const std::string &dir, const std::string &lockfile) {
    int ret =
        mkdir(dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IWGRP |
                               S_IXGRP | S_IROTH | S_IWOTH | S_IXOTH);
    if (ret < 0 && errno != EEXIST) {
      if (errno == EACCES)
        throw std::runtime_error("Use sudo");
      else
        throw std::runtime_error("Error: mkdir");
    }
    _lockfile = dir + lockfile;
    _linkfile = dir + lockfile + "-singlelinkfile";
    close(open(_lockfile.c_str(), O_WRONLY | O_APPEND | O_CREAT, 0644));
  }

  bool acquire(bool blocking = true, int timeout = -1) {
    if (blocking) {
      assert(timeout == -1);
      timeout = 1000000;
      while (timeout > 0) {
        int ret = link(_lockfile.c_str(), _linkfile.c_str());
        if (ret == 0)
          return true;
        else if (errno == EEXIST)
          continue;
        else if (errno == ENOENT) {
          printf("Lockfile not found. Retrying...\n");
          continue;
        } else
          throw std::runtime_error("link");
      }
      throw std::runtime_error("timeout");
    } else {
      while (true) {
        int ret = link(_lockfile.c_str(), _linkfile.c_str());
        if (ret == 0)
          return true;
        else if (errno == EEXIST)
          return false;
        else if (errno == ENOENT) {
          printf("Lockfile not found. Retrying...\n");
          continue;
        } else
          throw std::runtime_error("link");
      }
    }
  }

  void release() {
    int ret = unlink(_linkfile.c_str());
    if (ret == 0)
      return;
    else
      throw std::runtime_error("unlink");
  }
};

std::string dir;
int num_threads;
std::atomic<int> global_lock{0};

LinkLock get_lock() {
  static const std::string lock_dir = dir + "/./cpp_linklock1/";
  static const std::string lock_file = "lockfile";
  return LinkLock(lock_dir.c_str(), lock_file.c_str());
}

std::string read_last_line_of_file(const std::string &filename) {
  using namespace std;
  // Get last line of file
  // https://stackoverflow.com/a/11877478
  ifstream fin;
  fin.open(filename);
  if (fin.is_open()) {
    fin.seekg(-1, ios_base::end); // go to one spot before the EOF

    bool keepLooping = true;
    while (keepLooping) {
      char ch;
      fin.get(ch); // Get current byte's data

      if ((int)fin.tellg() <= 1) { // If the data was at or before the 0th byte
        fin.seekg(0);              // The first line is the last line
        keepLooping = false;       // So stop there
      } else if (ch == '\n') {     // If the data was a newline
        keepLooping = false;       // Stop at the current position.
      } else { // If the data was neither a newline nor at the 0 byte
        fin.seekg(-2, ios_base::cur); // Move to the front of that data, then to
                                      // the front of the data before it
      }
    }

    string lastLine;
    getline(fin, lastLine); // Read the current line
    fin.close();
    return lastLine;

  } else {
    throw std::runtime_error("open");
  }
}

void read_and_write_val(const std::string &filename) {
  const std::string lastLine = read_last_line_of_file(filename);
  int fd = open(filename.c_str(), O_WRONLY | O_APPEND);
  if (fd < 0)
    throw std::runtime_error("open");

  int last = stoi(lastLine);
  last += 1;
  const std::string what_to_write = "\n" + std::to_string(last);
  write(fd, what_to_write.c_str(), what_to_write.size());
  fsync(fd);
  close(fd);
}

void increment_append(const std::string &filename) {
  while (!global_lock) {
    //   for (int i = 0; i < 100; i++) {
    LinkLock l = get_lock();
    l.acquire();
    read_and_write_val(filename);
    l.release();
  }
}

int main(int argc, const char *argv[]) {
  if (argc != 3) {
    printf("%s dir num_threads", argv[0]);
    exit(1);
  }

  global_lock = 0;

  dir = argv[1];
  num_threads = std::stoi(argv[2]);
  int seconds = 10;
  const std::string datafile = "cpplinklock-datafile";

  int fd = open(datafile.c_str(), O_WRONLY | O_TRUNC | O_CREAT, 0644);
  if (fd < 0)
    throw std::runtime_error("open");
  std::string initial_value = "0";
  write(fd, initial_value.c_str(), initial_value.size());
  fsync(fd);
  close(fd);

  std::vector<std::thread> threads;
  threads.reserve(num_threads);

  for (int i = 0; i < num_threads; i++) {
    threads.emplace_back(increment_append, datafile);
  }

  sleep(seconds);
  global_lock = 1;

  for (int i = 0; i < num_threads; i++) {
    threads.at(i).join();
  }

  std::string last_line = read_last_line_of_file(datafile);
  printf("Locktype: linklock1, Threads: %d, Seconds: %d, Locks acquired: %s\n",
         num_threads, seconds, last_line.c_str());
}